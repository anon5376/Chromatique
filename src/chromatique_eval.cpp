// Chromatique's fully learned evaluator for the isolated Stockfish-19 fork.
// GPL-3.0-or-later. Stockfish NNUE evaluation is never called.
#include "chromatique_eval.h"
#include "misc.h"
#ifdef __APPLE__
#include <mach-o/dyld.h>
#endif
#include "uci.h"
#include "movegen.h"
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <unordered_map>
namespace Stockfish::Chromatique {
namespace {
constexpr int N=820,H=512,K=32,P=1968;
struct Model {std::vector<float> data;std::unordered_map<std::string,int> moves;std::string sha,path;unsigned generation=0;};
Model net;
std::filesystem::path executable_directory;
[[noreturn]] void fail(const std::string& message){std::cerr<<"Chromatique model error: "<<message<<std::endl;std::exit(1);}
constexpr int O_B1=N*H,O_W2=O_B1+H,O_B2=O_W2+H*K,O_VALUE=O_B2+K,O_VBIAS=O_VALUE+K,O_LINEAR=O_VBIAS+1,O_LBIAS=O_LINEAR+N,O_POLICY=O_LBIAS+1,O_PBIAS=O_POLICY+H*P,O_TEMP=O_PBIAS+P,COUNT=O_TEMP+1;
void first_layer(const std::array<float,N>& x,std::array<float,H>& h,float& direct){
    const float* w=net.data.data();for(int j=0;j<H;++j)h[j]=w[O_B1+j];direct=w[O_LBIAS];
    for(int i=0;i<N;++i)if(x[i]!=0){float v=x[i];direct+=w[O_LINEAR+i]*v;const float* column=w+i*H;for(int j=0;j<H;++j)h[j]+=column[j]*v;}
    for(float& v:h)v=std::max(0.0f,v);
}
float dot(const float* w,const float* h){float a=0,b=0,c=0,d=0;for(int i=0;i<H;i+=4){a+=w[i]*h[i];b+=w[i+1]*h[i+1];c+=w[i+2]*h[i+2];d+=w[i+3]*h[i+3];}return (a+b)+(c+d);}
}
// Standalone packaging, 2026-10-19: locate the unchanged model independently of GUI working directory.
void initialize_executable_path(const std::filesystem::path& input){
    namespace fs=std::filesystem;fs::path executable=input;std::error_code error;
#ifdef __APPLE__
    std::uint32_t size=0;_NSGetExecutablePath(nullptr,&size);std::vector<char> buffer(size);
    if(_NSGetExecutablePath(buffer.data(),&size)==0)executable=buffer.data();
#elif defined(__linux__)
    auto actual=fs::read_symlink("/proc/self/exe",error);if(!error)executable=actual;
#elif defined(_WIN32)
    executable=CommandLine::get_binary_directory(input)/input.filename();
#endif
    error.clear();auto canonical=fs::weakly_canonical(executable,error);
    executable_directory=(error?fs::absolute(executable):canonical).parent_path();
}
std::string default_path(){
    if(const char* p=std::getenv("CHROMATIQUE_NATIVE_MODEL");p&&*p)return p;
    auto model=executable_directory.parent_path()/"weights"/"chromatique-v4.native";
    auto adjacent=executable_directory/"weights"/"chromatique-v4.native";
    if(std::filesystem::is_regular_file(adjacent))model=adjacent;
    auto utf8=model.u8string();return std::string(utf8.begin(),utf8.end());
}
void load(const std::filesystem::path& path){
    std::ifstream f(path,std::ios::binary);if(!f)fail("cannot open "+path.string());
    char magic[8],sha[64];std::uint32_t dims[4];std::uint64_t expected;
    f.read(magic,8);f.read(reinterpret_cast<char*>(dims),16);f.read(sha,64);f.read(reinterpret_cast<char*>(&expected),8);
    if(!f||std::memcmp(magic,"CHROMA3\0",8)||dims[0]!=N||dims[1]!=H||dims[2]!=K||dims[3]!=P)fail("incompatible header");
    std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(f)),{});
    if(bytes.size()!=COUNT*sizeof(float)+P*6)fail("truncated/trailing model data");
    std::uint64_t checksum=14695981039346656037ull;for(auto b:bytes)checksum=(checksum^b)*1099511628211ull;
    if(checksum!=expected)fail("checksum mismatch");
    net.data.resize(COUNT);std::memcpy(net.data.data(),bytes.data(),COUNT*sizeof(float));
    for(float v:net.data)if(!std::isfinite(v))fail("non-finite parameter");
    if(net.data[O_TEMP]<=0)fail("invalid policy temperature");
    net.moves.clear();const char* names=reinterpret_cast<const char*>(bytes.data()+COUNT*sizeof(float));
    for(int i=0;i<P;++i){std::string name(names+i*6,strnlen(names+i*6,6));if(name.size()<4||name.size()>5||!net.moves.emplace(name,i).second)fail("invalid vocabulary");}
    net.sha=std::string(sha,64);net.path=path.string();net.generation++;
}
void ensure_loaded(){if(net.data.size()!=COUNT)fail("no trained model loaded; Stockfish fallback forbidden");}
std::array<float,N> features(const Position& pos){
    std::array<float,N> x{};Color us=pos.side_to_move();int kings[2]={-1,-1},count[12]={},sumOwn[12]={},sumEnemy[12]={};
    for(int s=0;s<64;++s){Piece p=pos.piece_on(Square(s));if(p==NO_PIECE)continue;int plane=int(type_of(p))-1+(color_of(p)==us?0:6),sq=us==WHITE?s:s^56;x[plane*64+sq]=1;count[plane]++;if(type_of(p)==KING)kings[color_of(p)==us?0:1]=sq;}
    if(kings[0]<0||kings[1]<0)fail("missing king");
    x[768]=1;x[769]=bool(pos.can_castle(us==WHITE?WHITE_OO:BLACK_OO));x[770]=bool(pos.can_castle(us==WHITE?WHITE_OOO:BLACK_OOO));x[771]=bool(pos.can_castle(us==WHITE?BLACK_OO:WHITE_OO));x[772]=bool(pos.can_castle(us==WHITE?BLACK_OOO:WHITE_OOO));
    Square ep=pos.state()->chromatiqueEp;x[773]=ep==SQ_NONE?-1.0f:float((int(file_of(ep))+1)/8.0);x[774]=float(std::min(100,pos.rule50_count())/100.0);x[775]=pos.state()->repetition!=0;
    int af=kings[0]%8,ar=kings[0]/8,bf=kings[1]%8,br=kings[1]/8;
    x[776]=float(af/7.0);x[777]=float(ar/7.0);x[778]=float(bf/7.0);x[779]=float(br/7.0);x[780]=float(std::max(std::abs(af-bf),std::abs(ar-br))/7.0);x[781]=float(std::min({af,7-af,ar,7-ar})/3.0);x[782]=float(std::min({bf,7-bf,br,7-br})/3.0);
    int occupied=0;for(int p=0;p<12;++p){occupied+=count[p];for(int s=0;s<64;++s)if(x[p*64+s]){sumOwn[p]+=std::max(std::abs(s%8-af),std::abs(s/8-ar));sumEnemy[p]+=std::max(std::abs(s%8-bf),std::abs(s/8-br));}x[784+p]=float(count[p]/8.0);if(count[p]){x[796+p]=float(double(sumOwn[p])/count[p]/7.0);x[808+p]=float(double(sumEnemy[p])/count[p]/7.0);}}
    x[783]=float(occupied/32.0);return x;
}
double centipawns(const Position& pos){
    ensure_loaded();struct Entry {Key key=0;double cp=0;unsigned generation=0;};static thread_local std::array<Entry,16384> cache;
    Key key=pos.key();auto& entry=cache[key&16383];if(entry.generation==net.generation&&entry.key==key)return entry.cp;
    auto x=features(pos);std::array<float,H> h;float direct;first_layer(x,h,direct);const float* w=net.data.data();float value=w[O_VBIAS]+direct;
    for(int j=0;j<K;++j){float z=w[O_B2+j]+dot(w+O_W2+j*H,h.data());value+=w[O_VALUE+j]*std::max(0.0f,z);}
    double cp=std::clamp(600.0*value,-10000.0,10000.0);entry={key,cp,net.generation};return cp;
}
Value evaluate(const Position& pos){return UCIEngine::from_cp(centipawns(pos),pos);}
bool policy_enabled(){const char* p=std::getenv("CHROMATIQUE_POLICY");return !p||std::strcmp(p,"0");}
std::vector<double> policy(const Position& pos,const std::vector<Move>& moves){
    ensure_loaded();auto x=features(pos);std::array<float,H> h;float direct;first_layer(x,h,direct);std::vector<double> scores;const float* w=net.data.data();
    for(Move move:moves){std::string name=UCIEngine::move(move,pos.is_chess960());if(pos.side_to_move()==BLACK){name[1]=char('9'-name[1]+'0');name[3]=char('9'-name[3]+'0');}auto found=net.moves.find(name);if(found==net.moves.end())fail("move outside vocabulary: "+name);int k=found->second;float z=w[O_PBIAS+k]+dot(w+O_POLICY+k*H,h.data());scores.push_back(z/w[O_TEMP]);}return scores;
}
std::string metadata(){ensure_loaded();std::ostringstream s;s<<"{\"name\":\"Chromatique v4\",\"model_sha256\":\""<<net.sha<<"\",\"search_kind\":\"stockfish19_native\",\"evaluation_kind\":\"fully_neural\",\"classical_evaluation\":false,\"fixed_material\":false,\"architecture\":[820,512,32],\"policy_enabled\":"<<(policy_enabled()?"true":"false")<<"}";return s.str();}
std::string trace(const Position& pos){ensure_loaded();auto x=features(pos);std::ostringstream s;s<<std::setprecision(17)<<"chromatique {\"cp\":"<<centipawns(pos)<<",\"features\":[";for(int i=0;i<N;++i){if(i)s<<',';s<<x[i];}s<<"],\"internal\":"<<evaluate(pos)<<",\"roundtrip_cp\":"<<UCIEngine::to_cp(evaluate(pos),pos)<<",\"model_sha256\":\""<<net.sha<<"\",\"policy\":[";std::vector<Move> moves;for(Move m:MoveList<LEGAL>(pos))moves.push_back(m);auto logits=policy(pos,moves);for(usize i=0;i<moves.size();++i){if(i)s<<',';s<<"{\"move\":\""<<UCIEngine::move(moves[i],pos.is_chess960())<<"\",\"logit\":"<<logits[i]<<"}";}s<<"]}";return s.str();}
}
